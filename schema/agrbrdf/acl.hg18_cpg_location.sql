--
-- Name: hg18_cpg_location; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE hg18_cpg_location FROM PUBLIC;
REVOKE ALL ON TABLE hg18_cpg_location FROM agrbrdf;
GRANT ALL ON TABLE hg18_cpg_location TO agrbrdf;
GRANT SELECT ON TABLE hg18_cpg_location TO gbs;


