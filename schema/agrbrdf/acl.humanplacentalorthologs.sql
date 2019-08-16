--
-- Name: humanplacentalorthologs; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE humanplacentalorthologs FROM PUBLIC;
REVOKE ALL ON TABLE humanplacentalorthologs FROM agrbrdf;
GRANT ALL ON TABLE humanplacentalorthologs TO agrbrdf;
GRANT SELECT ON TABLE humanplacentalorthologs TO gbs;


