--
-- Name: blastx_results; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE blastx_results FROM PUBLIC;
REVOKE ALL ON TABLE blastx_results FROM agrbrdf;
GRANT ALL ON TABLE blastx_results TO agrbrdf;
GRANT SELECT ON TABLE blastx_results TO gbs;


