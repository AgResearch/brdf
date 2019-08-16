--
-- Name: bovine_est_entropies; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE bovine_est_entropies FROM PUBLIC;
REVOKE ALL ON TABLE bovine_est_entropies FROM agrbrdf;
GRANT ALL ON TABLE bovine_est_entropies TO agrbrdf;
GRANT SELECT ON TABLE bovine_est_entropies TO gbs;


