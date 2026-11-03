import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "/api";

function App() {
    const displayValue = (value) => {
    if (value === null || value === undefined) {
      return "-";
    }

    if (typeof value === "object") {
      return (
        value.name ||
        value.code ||
        value.label ||
        value.number ||
        "-"
      );
    }

    return String(value);
  };
  const [dashboard, setDashboard] = useState(null);

  const [orderNumber, setOrderNumber] = useState("WO-2026-000001");
  const [traceData, setTraceData] = useState(null);

  const [lotNumber, setLotNumber] = useState("");
  const [lotTraceData, setLotTraceData] = useState(null);

  const [loadingDashboard, setLoadingDashboard] = useState(true);
  const [loadingOrder, setLoadingOrder] = useState(false);
  const [loadingLot, setLoadingLot] = useState(false);

  const [orderError, setOrderError] = useState("");
  const [lotError, setLotError] = useState("");

  // ============================================================
  // LOAD DASHBOARD
  // ============================================================

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoadingDashboard(true);

      const response = await axios.get(
        `${API_BASE}/dashboard/`
      );

      setDashboard(response.data);
    } catch (error) {
      console.error("Dashboard error:", error);
    } finally {
      setLoadingDashboard(false);
    }
  };

  // ============================================================
  // TRACE PRODUCTION ORDER
  // ============================================================

  const traceProductionOrder = async () => {
    if (!orderNumber.trim()) {
      setOrderError("Please enter a production order.");
      return;
    }

    try {
      setLoadingOrder(true);
      setOrderError("");
      setTraceData(null);

      const response = await axios.get(
        `${API_BASE}/traceability/${encodeURIComponent(
          orderNumber.trim()
        )}/`
      );

      setTraceData(response.data);
    } catch (error) {
      console.error("Traceability error:", error);

      if (error.response?.data?.error) {
        setOrderError(error.response.data.error);
      } else {
        setOrderError(
          "Unable to trace this production order."
        );
      }
    } finally {
      setLoadingOrder(false);
    }
  };

  // ============================================================
  // TRACE MATERIAL LOT
  // ============================================================

  const traceMaterialLot = async () => {
    if (!lotNumber.trim()) {
      setLotError("Please enter a material lot number.");
      return;
    }

    try {
      setLoadingLot(true);
      setLotError("");
      setLotTraceData(null);

      const response = await axios.get(
        `${API_BASE}/lot-traceability/${encodeURIComponent(
          lotNumber.trim()
        )}/`
      );

      setLotTraceData(response.data);
    } catch (error) {
      console.error("Lot traceability error:", error);

      if (error.response?.data?.error) {
        setLotError(error.response.data.error);
      } else {
        setLotError(
          "Unable to trace this material lot."
        );
      }
    } finally {
      setLoadingLot(false);
    }
  };

  // ============================================================
  // FORMAT NUMBER
  // ============================================================

  const formatNumber = (value) => {
    if (value === null || value === undefined) {
      return "0";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
      return value;
    }

    return number.toLocaleString();
  };

  // ============================================================
  // LOADING
  // ============================================================

  if (loadingDashboard) {
    return (
      <div className="loading-screen">
        <div className="loading-box">
          Loading Manufacturing Traceability...
        </div>
      </div>
    );
  }

  // ============================================================
  // SAFE DASHBOARD DATA
  // ============================================================

  const masterData = dashboard?.master_data || {};
  const production = dashboard?.production || {};
  const quality = dashboard?.quality || {};
  const correctiveActions =
    dashboard?.corrective_actions || {};

  const defectsByStatus =
    quality.defects_by_status || {};

  const defectsBySeverity =
    quality.defects_by_severity || {};

  return (
    <div className="app">

      {/* ======================================================
          HEADER
      ====================================================== */}

      <header className="top-header">
        <div className="header-content">
          <h1>Manufacturing Traceability</h1>
          <p>
            Quality &amp; Production Traceability System
          </p>
        </div>
      </header>

      {/* ======================================================
          MAIN DASHBOARD
      ====================================================== */}

      <main className="dashboard-container">

        {/* Dashboard Heading */}

        <section className="dashboard-title">
          <h2>Operations Dashboard</h2>
          <p>
            Manufacturing and quality overview
          </p>
        </section>

        {/* ====================================================
            METRIC CARDS
        ==================================================== */}

        <section className="metrics-grid">

          <div className="metric-card">
            <span>Products</span>
            <strong>
              {formatNumber(masterData.products)}
            </strong>
          </div>

          <div className="metric-card">
            <span>Suppliers</span>
            <strong>
              {formatNumber(masterData.suppliers)}
            </strong>
          </div>

          <div className="metric-card">
            <span>Material Lots</span>
            <strong>
              {formatNumber(masterData.material_lots)}
            </strong>
          </div>

          <div className="metric-card">
            <span>Production Orders</span>
            <strong>
              {formatNumber(
                production.production_orders
              )}
            </strong>
          </div>

          <div className="metric-card">
            <span>Inspections</span>
            <strong>
              {formatNumber(quality.inspections)}
            </strong>
          </div>

          <div className="metric-card danger-card">
            <span>Total Defects</span>
            <strong>
              {formatNumber(quality.defects)}
            </strong>
          </div>

          <div className="metric-card warning-card">
            <span>Defect Rate</span>
            <strong>
              {quality.defect_rate_percent || 0}%
            </strong>
          </div>

          <div className="metric-card">
            <span>Total CAPA</span>
            <strong>
              {formatNumber(correctiveActions.total)}
            </strong>
          </div>

        </section>

        {/* ====================================================
            QUALITY SUMMARY
        ==================================================== */}

        <section className="quality-grid">

          {/* Defects by Status */}

          <div className="summary-card">

            <h2>Defects by Status</h2>

            <div className="stat-row">
              <span>Open</span>
              <strong>
                {formatNumber(defectsByStatus.open)}
              </strong>
            </div>

            <div className="stat-row">
              <span>Contained</span>
              <strong>
                {formatNumber(
                  defectsByStatus.contained
                )}
              </strong>
            </div>

            <div className="stat-row">
              <span>Resolved</span>
              <strong>
                {formatNumber(
                  defectsByStatus.resolved
                )}
              </strong>
            </div>

            <div className="stat-row">
              <span>Closed</span>
              <strong>
                {formatNumber(
                  defectsByStatus.closed
                )}
              </strong>
            </div>

          </div>

          {/* Defects by Severity */}

          <div className="summary-card">

            <h2>Defects by Severity</h2>

            <div className="stat-row critical">
              <span>Critical</span>
              <strong>
                {formatNumber(
                  defectsBySeverity.critical
                )}
              </strong>
            </div>

            <div className="stat-row high">
              <span>High</span>
              <strong>
                {formatNumber(
                  defectsBySeverity.high
                )}
              </strong>
            </div>

          </div>

          {/* CAPA */}

          <div className="summary-card">

            <h2>Corrective Actions</h2>

            <div className="stat-row">
              <span>Open</span>
              <strong>
                {formatNumber(
                  correctiveActions.open
                )}
              </strong>
            </div>

            <div className="stat-row">
              <span>In Progress</span>
              <strong>
                {formatNumber(
                  correctiveActions.in_progress
                )}
              </strong>
            </div>

            <div className="stat-row">
              <span>Pending Verification</span>
              <strong>
                {formatNumber(
                  correctiveActions.pending_verification
                )}
              </strong>
            </div>

            <div className="stat-row">
              <span>Closed</span>
              <strong>
                {formatNumber(
                  correctiveActions.closed
                )}
              </strong>
            </div>

          </div>

        </section>

        {/* ====================================================
            PRODUCTION ORDER SEARCH
        ==================================================== */}

        <section className="search-card">

          <h2>Trace Production Order</h2>

          <div className="search-row">

            <input
              type="text"
              value={orderNumber}
              onChange={(e) =>
                setOrderNumber(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  traceProductionOrder();
                }
              }}
              placeholder="Example: WO-2026-000001"
            />

            <button
              onClick={traceProductionOrder}
              disabled={loadingOrder}
            >
              {loadingOrder ? "Tracing..." : "Trace"}
            </button>

          </div>

          {orderError && (
            <div className="error-message">
              {orderError}
            </div>
          )}

        </section>

        {/* ====================================================
            PRODUCTION ORDER RESULT
        ==================================================== */}

        {traceData && (
          <section className="trace-section">

            <div className="section-heading">
              <h2>Production Order</h2>
            </div>

            <div className="order-summary">

              <div>
                <span>Order</span>
                <strong>
                  {
                    traceData.production_order
                      ?.order_number
                  }
                </strong>
              </div>

              <div>
                <span>Product</span>
                <strong>
                  {
                    traceData.production_order
                      ?.product?.sku
                  }
                </strong>
              </div>

              <div>
                <span>Status</span>
                <strong>
                  {
                    traceData.production_order
                      ?.status
                  }
                </strong>
              </div>

              <div>
                <span>BOM</span>
                <strong>
                  Version{" "}
                  {
                    traceData.production_order
                      ?.bom_version
                  }
                </strong>
              </div>

            </div>

            {/* Material Traceability */}

            <div className="data-card">

              <h2>Material Traceability</h2>

              <div className="table-container">

                <table>

                  <thead>
                    <tr>
                      <th>Material</th>
                      <th>Lot</th>
                      <th>Supplier</th>
                      <th>Received</th>
                      <th>Consumed</th>
                    </tr>
                  </thead>

                  <tbody>

                    {traceData.material_traceability
                      ?.length > 0 ? (
                      traceData.material_traceability.map(
                        (item, index) => (
                          <tr key={index}>

                            <td>
                              {item.material_code}
                            </td>

                            <td className="lot-cell">
                              {item.lot_number}
                            </td>

                            <td>
                              {item.supplier_code}
                            </td>

                            <td>
                              {item.received_quantity}
                            </td>

                            <td>
                              {item.consumed_quantity}
                            </td>

                          </tr>
                        )
                      )
                    ) : (
                      <tr>
                        <td
                          colSpan="5"
                          className="empty-cell"
                        >
                          No material traceability
                          records found.
                        </td>
                      </tr>
                    )}

                  </tbody>

                </table>

              </div>

            </div>

            {/* Quality Traceability */}

            <div className="data-card">

              <h2>Quality Traceability</h2>

              {traceData.quality_traceability
                ?.length > 0 ? (

                traceData.quality_traceability.map(
                  (inspection, index) => (

                    <div
                      className="inspection-card"
                      key={index}
                    >

                      <div className="inspection-header">

                        <div>
                          <span>
                            Inspection
                          </span>

                          <strong>
                            {
                              inspection.inspection_number
                            }
                          </strong>
                        </div>

                        <div>
                          <span>Result</span>

                          <strong
                            className={
                              inspection.result ===
                              "FAIL"
                                ? "status-fail"
                                : "status-pass"
                            }
                          >
                            {inspection.result}
                          </strong>
                        </div>

                        <div>
                          <span>Failed Quantity</span>

                          <strong>
                            {
                              inspection.failed_quantity
                            }
                          </strong>
                        </div>

                      </div>

                      {inspection.defects
                        ?.length > 0 && (

                        <div className="defect-list">

                          {inspection.defects.map(
                            (
                              defect,
                              defectIndex
                            ) => (

                              <div
                                className="defect-item"
                                key={defectIndex}
                              >

                                <div>
                                  <span>
                                    Defect
                                  </span>

                                  <strong>
                                    {
                                      defect.defect_number
                                    }
                                  </strong>
                                </div>

                                <div>
                                  <span>
                                    Type
                                  </span>

                                  <strong>
                                    {
                                      defect.defect_type
                                    }
                                  </strong>
                                </div>

                                <div>
                                  <span>
                                    Severity
                                  </span>

                                  <strong>
                                    {
                                      defect.severity
                                    }
                                  </strong>
                                </div>

                                <div>
                                  <span>
                                    Quantity
                                  </span>

                                  <strong>
                                    {
                                      defect.quantity
                                    }
                                  </strong>
                                </div>

                                <div>
  <span>Process</span>
  <strong>
    {typeof defect.process_step === "object"
      ? defect.process_step?.name ||
        defect.process_step?.code ||
        "-"
      : defect.process_step || "-"}
  </strong>
</div>

<div>
  <span>Machine</span>
  <strong>
    {typeof defect.machine === "object"
      ? defect.machine?.name ||
        defect.machine?.code ||
        "-"
      : defect.machine || "-"}
  </strong>
</div>

                              </div>

                            )
                          )}

                        </div>

                      )}

                    </div>

                  )
                )

              ) : (

                <div className="empty-state">
                  No quality traceability records
                  found.
                </div>

              )}

            </div>

          </section>
        )}

        {/* ====================================================
            MATERIAL LOT SEARCH
        ==================================================== */}

        <section className="search-card">

          <h2>Trace Material Lot</h2>

          <p className="search-description">
            Trace a supplier material lot downstream
            into production orders, inspections,
            defects, machines and corrective actions.
          </p>

          <div className="search-row">

            <input
              type="text"
              value={lotNumber}
              onChange={(e) =>
                setLotNumber(e.target.value)
              }
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  traceMaterialLot();
                }
              }}
              placeholder="Example: LOT-SUP-0004-2026-000792"
            />

            <button
              onClick={traceMaterialLot}
              disabled={loadingLot}
            >
              {loadingLot ? "Tracing..." : "Trace Lot"}
            </button>

          </div>

          {lotError && (
            <div className="error-message">
              {lotError}
            </div>
          )}

        </section>

        {/* ====================================================
            MATERIAL LOT RESULT
        ==================================================== */}

        {lotTraceData && (
          <section className="trace-section">

            <div className="section-heading">
              <h2>Material Lot Traceability</h2>
            </div>

            {/* Lot information */}

            <div className="lot-summary">

              <div>
                <span>Lot Number</span>
                <strong>
                  {
                    lotTraceData.material_lot
                      ?.lot_number
                  }
                </strong>
              </div>

              <div>
                <span>Material</span>
                <strong>
                  {
                    lotTraceData.material_lot
                      ?.material_code
                  }
                </strong>
              </div>

              <div>
                <span>Supplier</span>
                <strong>
                  {
                    lotTraceData.material_lot
                      ?.supplier_code
                  }
                </strong>
              </div>

              <div>
                <span>Received Quantity</span>
                <strong>
                  {
                    lotTraceData.material_lot
                      ?.received_quantity
                  }
                </strong>
              </div>

              <div>
                <span>Status</span>
                <strong>
                  {
                    lotTraceData.material_lot
                      ?.status
                  }
                </strong>
              </div>

            </div>

            {/* Downstream Orders */}

            <div className="data-card">

              <h2>Downstream Production Orders</h2>

              {lotTraceData
                .downstream_traceability
                ?.length > 0 ? (

                lotTraceData.downstream_traceability.map(
                  (order, index) => (

                    <div
                      className="downstream-order"
                      key={index}
                    >

                      <div className="downstream-header">

                        <div>
                          <span>
                            Production Order
                          </span>

                          <strong>
                            {order.order_number}
                          </strong>
                        </div>

                        <div>
                          <span>Product</span>

                          <strong>
                            {order.product_sku}
                          </strong>
                        </div>

                        <div>
                          <span>Consumed</span>

                          <strong>
                            {order.consumed_quantity}
                          </strong>
                        </div>

                        <div>
                          <span>Status</span>

                          <strong>
                            {order.order_status}
                          </strong>
                        </div>

                      </div>

                      {order.inspections_with_defects
                        ?.length > 0 ? (

                        <div className="lot-inspections">

                          <h3>
                            Quality Findings
                          </h3>

                          {order.inspections_with_defects.map(
                            (
                              inspection,
                              inspectionIndex
                            ) => (

                              <div
                                className="lot-inspection"
                                key={
                                  inspectionIndex
                                }
                              >

                                <div className="inspection-line">

                                  <strong>
                                    {
                                      inspection.inspection_number
                                    }
                                  </strong>

                                  <span
                                    className={
                                      inspection.result ===
                                      "FAIL"
                                        ? "status-fail"
                                        : "status-pass"
                                    }
                                  >
                                    {
                                      inspection.result
                                    }
                                  </span>

                                  <span>
                                    Failed:{" "}
                                    {
                                      inspection.failed_quantity
                                    }
                                  </span>

                                </div>

                                {inspection.defects?.map(
                                  (
                                    defect,
                                    defectIndex
                                  ) => (

                                    <div
                                      className="lot-defect"
                                      key={
                                        defectIndex
                                      }
                                    >

                                      <div>
                                        <span>
                                          Defect
                                        </span>

                                        <strong>
                                          {
                                            defect.defect_number
                                          }
                                        </strong>
                                      </div>

                                      <div>
                                        <span>
                                          Type
                                        </span>

                                        <strong>
                                          {
                                            defect.defect_type
                                          }
                                        </strong>
                                      </div>

                                      <div>
                                        <span>
                                          Severity
                                        </span>

                                        <strong>
                                          {
                                            defect.severity
                                          }
                                        </strong>
                                      </div>

                                      <div>
                                        <span>
                                          Process
                                        </span>

                                        <strong>
                                          {
                                            defect.process_step
                                          }
                                        </strong>
                                      </div>

                                      <div>
                                        <span>
                                          Machine
                                        </span>

                                        <strong>
                                          {
                                            defect.machine
                                          }
                                        </strong>
                                      </div>

                                    </div>

                                  )
                                )}

                              </div>

                            )
                          )}

                        </div>

                      ) : (

                        <div className="no-defects">
                          No defects found for this
                          production order.
                        </div>

                      )}

                    </div>

                  )
                )

              ) : (

                <div className="empty-state">
                  No downstream production orders
                  found for this material lot.
                </div>

              )}

            </div>

          </section>
        )}

      </main>

      {/* ======================================================
          FOOTER
      ====================================================== */}

      <footer className="footer">
        Manufacturing Traceability &amp; Quality
        Management System
      </footer>

    </div>
  );
}

export default App;